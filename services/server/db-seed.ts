
import { db } from './db.js';
import { 
  users, 
  tradingAccounts, 
  tradingBots, 
  educationalResources 
} from '@shared/schema';

/**
 * Seeds the database with initial data, including a demo user, trading account,
 * trading bots, and educational resources.
 */
async function seed() {
  console.log('🌱 Seeding database...');

  try {
    // Create demo user
    const [user] = await db.insert(users).values({
      email: 'demo@genztradingbot.com',
      username: 'demo_trader',
      passwordHash: 'demo_password_hash',
      firstName: 'Demo',
      lastName: 'Trader'
    }).returning();

    console.log('✅ Created demo user');

    // Create demo trading account
    await db.insert(tradingAccounts).values({
      userId: user.id,
      platform: 'bybit',
      accountId: 'demo_account_123',
      accountName: 'Demo Trading Account',
      balance: '10000.00',
      currency: 'USDT'
    });

    console.log('✅ Created demo trading account');

    // Create demo trading bots
    await db.insert(tradingBots).values([
      {
        userId: user.id,
        accountId: 1,
        name: 'Scalping Bot Pro',
        strategy: 'scalping',
        symbols: ['BTCUSDT', 'ETHUSDT'],
        parameters: {
          riskLevel: 0.02,
          stopLoss: 0.01,
          takeProfit: 0.02,
          timeframe: '1m'
        },
        status: 'stopped'
      },
      {
        userId: user.id,
        accountId: 1,
        name: 'Grid Trading Bot',
        strategy: 'grid',
        symbols: ['ADAUSDT', 'DOTUSDT'],
        parameters: {
          gridSpacing: 0.005,
          orderAmount: 100,
          maxOrders: 10
        },
        status: 'running'
      }
    ]);

    console.log('✅ Created demo trading bots');

    // Create sample educational resources
    await db.insert(educationalResources).values([
      {
        title: 'Getting Started with Algorithmic Trading',
        description: 'Learn the basics of automated trading systems',
        url: 'https://example.com/trading-basics',
        type: 'course',
        skillLevel: 'beginner',
        category: 'Trading Fundamentals',
        tags: ['trading', 'automation', 'basics'],
        rating: '4.8'
      },
      {
        title: 'Advanced Risk Management Strategies',
        description: 'Master risk management in trading bots',
        url: 'https://example.com/risk-management',
        type: 'article',
        skillLevel: 'advanced',
        category: 'Risk Management',
        tags: ['risk', 'management', 'advanced'],
        rating: '4.9'
      }
    ]);

    console.log('✅ Created sample educational resources');
    console.log('🎉 Database seeding completed successfully!');

  } catch (error) {
    console.error('❌ Database seeding failed:', error);
    process.exit(1);
  }
}

seed();
